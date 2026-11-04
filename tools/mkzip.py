import zipfile,os,sys
out=sys.argv[1];B='build'
files=[('AndroidManifest.xml',True),('classes.dex',True),('resources.arsc',False),('res/drawable/icon.png',False)]
for root,_,fs in os.walk(B+'/assets'):
    for f in sorted(fs):
        rel=os.path.relpath(os.path.join(root,f),B); files.append((rel, not f.endswith('.woff2')))
with zipfile.ZipFile(out,'w') as z:
    for rel,comp in files:
        zi=zipfile.ZipInfo(rel,date_time=(2026,11,3,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED if comp else zipfile.ZIP_STORED
        data=open(os.path.join(B,rel),'rb').read()
        if not comp:
            # align stored data to 4 bytes using extra field padding
            off=z.fp.tell()+30+len(rel.encode())
            pad=(4-off%4)%4; zi.extra=b'\0'*pad
        z.writestr(zi,data)
print('zipped',len(files))
