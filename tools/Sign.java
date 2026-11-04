import com.android.apksig.ApkSigner;
import java.io.*; import java.security.*; import java.security.cert.X509Certificate; import java.util.*;
public class Sign {
  public static void main(String[] a) throws Exception {
    KeyStore ks = KeyStore.getInstance("PKCS12");
    char[] pw = a[2].toCharArray();
    ks.load(new FileInputStream(a[3]), pw);
    String alias = ks.aliases().nextElement();
    PrivateKey key = (PrivateKey) ks.getKey(alias, pw);
    X509Certificate cert = (X509Certificate) ks.getCertificate(alias);
    ApkSigner.SignerConfig sc = new ApkSigner.SignerConfig.Builder("kasa", key, Collections.singletonList(cert)).build();
    new ApkSigner.Builder(Collections.singletonList(sc)).setInputApk(new File(a[0])).setOutputApk(new File(a[1]))
      .setV1SigningEnabled(false).setV2SigningEnabled(true).setMinSdkVersion(24).build().sign();
    System.out.println("signed");
  }
}
