import struct
ANDROID_NS="http://schemas.android.com/apk/res/android"
ATTR_IDS={"theme":0x01010000,"label":0x01010001,"icon":0x01010002,"name":0x01010003,"exported":0x01010010,"configChanges":0x0101001f,
 "minSdkVersion":0x0101020c,"versionCode":0x0101021b,"versionName":0x0101021c,"windowSoftInputMode":0x0101022b,"targetSdkVersion":0x01010270,
 "allowBackup":0x01010280,"hardwareAccelerated":0x010102d3,"usesCleartextTraffic":0x010104ec,"fullBackupContent":0x01010473,"dataExtractionRules":0x0101063e}
T_REF,T_STR,T_DEC,T_HEX,T_BOOL=0x01,0x03,0x10,0x11,0x12

def pad4(b): return b+b"\0"*((4-len(b)%4)%4)

def strpool_utf16(strs):
    offs=[];data=b""
    for s in strs:
        offs.append(len(data)); u=s.encode("utf-16le"); data+=struct.pack("<H",len(u)//2)+u+b"\0\0"
    data=pad4(data)
    hdr=28; start=hdr+4*len(strs)
    body=b"".join(struct.pack("<I",o) for o in offs)+data
    return struct.pack("<HHIIIIII",0x0001,hdr,hdr+len(body),len(strs),0,0,start,0)+body

def strpool_utf8(strs):
    offs=[];data=b""
    for s in strs:
        offs.append(len(data)); u=s.encode("utf-8"); assert len(s)<128 and len(u)<128
        data+=bytes([len(s),len(u)])+u+b"\0"
    data=pad4(data)
    hdr=28; start=hdr+4*len(strs)
    body=b"".join(struct.pack("<I",o) for o in offs)+data
    return struct.pack("<HHIIIIII",0x0001,hdr,hdr+len(body),len(strs),0,0x100,start,0)+body

# element tree: (tag, [(ns, name, kind, value)], [children])
def axml(tree):
    # collect android attribute names first (resource map), then other strings
    attr_names=[];others=[]
    def walk(el):
        tag,attrs,kids=el
        for ns,name,kind,val in attrs:
            if ns and name not in attr_names: attr_names.append(name)
        for k in kids: walk(k)
    walk(tree)
    attr_names.sort(key=lambda n:ATTR_IDS[n])
    strs=list(attr_names)
    def S(x):
        if x not in strs: strs.append(x)
        return strs.index(x)
    S("android");S(ANDROID_NS)
    def collect(el):
        tag,attrs,kids=el; S(tag)
        for ns,name,kind,val in attrs:
            if not ns: S(name)
            if kind=="str": S(val)
        for k in kids: collect(k)
    collect(tree)
    chunks=[]
    pre=strs.index("android");uri=strs.index(ANDROID_NS)
    chunks.append(struct.pack("<HHIIiII",0x0100,16,24,1,-1,pre,uri))
    def emit(el):
        tag,attrs,kids=el
        A=[]
        for ns,name,kind,val in sorted(attrs,key=lambda a:(ATTR_IDS.get(a[1],0xffffffff) if a[0] else 0)):
            nsi=uri if ns else 0xffffffff; ni=strs.index(name)
            if kind=="str": raw=strs.index(val); t,d=T_STR,raw
            else:
                raw=0xffffffff; t={"ref":T_REF,"int":T_DEC,"hex":T_HEX,"bool":T_BOOL}[kind]
                d=(0xffffffff if val else 0) if kind=="bool" else val
            A.append(struct.pack("<IIIHBBI",nsi,ni,raw,8,0,t,d))
        body=struct.pack("<IIHHHHHH",0xffffffff,strs.index(tag),20,20,len(A),0,0,0)+b"".join(A)
        chunks.append(struct.pack("<HHIIi",0x0102,16,16+len(body),1,-1)+body)
        for k in kids: emit(k)
        chunks.append(struct.pack("<HHIIiII",0x0103,16,24,1,-1,0xffffffff,strs.index(tag)))
    emit(tree)
    chunks.append(struct.pack("<HHIIiII",0x0101,16,24,1,-1,pre,uri))
    sp=strpool_utf16(strs)
    rm=struct.pack("<HHI",0x0180,8,8+4*len(attr_names))+b"".join(struct.pack("<I",ATTR_IDS[n]) for n in attr_names)
    body=sp+rm+b"".join(chunks)
    return struct.pack("<HHI",0x0003,8,8+len(body))+body

def arsc(pkg_name, pkg_id, types):
    """types: list of (typeName, [(keyName, filePath)]) -> ids 0x7fTTEEEE"""
    gstrs=[];tstrs=[];kstrs=[]
    for tn,entries in types:
        tstrs.append(tn)
        for k,v in entries: kstrs.append(k); gstrs.append(v)
    gpool=strpool_utf8(gstrs)
    tpool=strpool_utf16(tstrs); kpool=strpool_utf16(kstrs)
    ptype=b""; gi=0; ki=0
    for ti,(tn,entries) in enumerate(types,1):
        n=len(entries)
        ptype+=struct.pack("<HHIBBHI",0x0202,16,16+4*n,ti,0,0,n)+b"\0"*(4*n)
        config=struct.pack("<I",64)+b"\0"*60
        hdr=20+64; start=hdr+4*n
        offs=b"".join(struct.pack("<I",16*i) for i in range(n))
        ents=b""
        for k,v in entries:
            ents+=struct.pack("<HHI",8,0,ki)+struct.pack("<HBBI",8,0,T_STR,gi); ki+=1; gi+=1
        ptype+=struct.pack("<HHIBBHII",0x0201,hdr,start+len(ents),ti,0,0,n,start)+config+offs+ents
    name=pkg_name.encode("utf-16le")[:254]; name+=b"\0"*(256-len(name))
    phdr=288
    body=tpool+kpool+ptype
    pkg=struct.pack("<HHII",0x0200,phdr,phdr+len(body),pkg_id)+name+struct.pack("<IIIII",phdr,len(types),phdr+len(tpool),len(kstrs),0)+body
    body=gpool+pkg
    return struct.pack("<HHII",0x0002,12,12+len(body),1)+body

if __name__=="__main__":
    E=lambda tag,attrs=(),kids=():(tag,list(attrs),list(kids))
    A=lambda name,kind,val:(True,name,kind,val)
    man=E("manifest",[(False,"package","str","app.kasa"),A("versionCode","int",6),A("versionName","str","1.5")],[
      E("uses-sdk",[A("minSdkVersion","int",24),A("targetSdkVersion","int",34)]),
      E("uses-permission",[A("name","str","android.permission.INTERNET")]),
      E("application",[A("label","str","Каса"),A("icon","ref",0x7f010000),A("allowBackup","bool",False),A("hardwareAccelerated","bool",True),A("usesCleartextTraffic","bool",False)],[
        E("activity",[A("name","str","app.kasa.MainActivity"),A("exported","bool",True),A("configChanges","hex",0x80|0x400|0x200|0x20|0x10|0x100|0x800),A("windowSoftInputMode","hex",0x10)],[
          E("intent-filter",[],[E("action",[A("name","str","android.intent.action.MAIN")]),E("category",[A("name","str","android.intent.category.LAUNCHER")])])])])])
    open("build/AndroidManifest.xml","wb").write(axml(man))
    open("build/resources.arsc","wb").write(arsc("app.kasa",0x7f,[("drawable",[("icon","res/drawable/icon.png")])]))
    print("ok")
