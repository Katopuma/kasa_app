#!/usr/bin/env bash
# Builds Kasa APK without the Android SDK: dx + android stubs from Maven Central, hand-written manifest/resources, apksig for v2 signing.
# Usage: KASA_KEYSTORE=path/to/key.p12 KASA_KEY_PASSWORD=... ./build.sh
set -euo pipefail
cd "$(dirname "$0")"
LIB=.cache/lib; FONTS=.cache/fonts
mkdir -p "$LIB" "$FONTS" build/assets/fonts build/res/drawable build/classes build/stubc

# 1. Java tools from Maven Central (dalvik-dx, android 4.1 stubs for compiling, apksig)
if [ ! -f "$LIB/apksig-2.3.0.jar" ]; then
  (cd tools && mvn -q dependency:copy-dependencies -DoutputDirectory="../$LIB" -DexcludeTransitive=true)
fi
# 2. Fonts from npm (bundled into the app, no network fonts at runtime)
if [ ! -d "$FONTS/fontsource-onest-5.3.1" ]; then
  (cd "$FONTS" && npm pack @fontsource/onest@5.3.1 @fontsource/unbounded@5.3.0 --silent >/dev/null && for f in *.tgz; do tar xzf "$f" --one-top-level="${f%.tgz}"; done)
fi
# 3. Web app -> build/assets/index.html (local storage, daily native rate fetch, bundled fonts)
python3 tools/mkhtml.py
# 4. Java -> dex
javac -nowarn --release 8 -d build/stubc android/stub/android/webkit/JavascriptInterface.java
javac -nowarn --release 8 -cp "$LIB/android-4.1.1.4.jar:build/stubc" -d build/classes android/src/app/kasa/MainActivity.java
java -cp "$LIB/dalvik-dx-16.0.1.jar" com.android.dx.command.Main --dex --min-sdk-version=24 --output=build/classes.dex build/classes
# 5. Binary manifest, resources.arsc, icon
cp res/drawable/icon.png build/res/drawable/icon.png
python3 tools/mkres.py
# 6. Package and sign (APK Signature Scheme v2)
python3 tools/mkzip.py build/unsigned.apk
javac -nowarn -cp "$LIB/apksig-2.3.0.jar" -d build/signer tools/Sign.java tools/Verify.java
X="--add-exports java.base/sun.security.x509=ALL-UNNAMED --add-exports java.base/sun.security.pkcs=ALL-UNNAMED --add-exports java.base/sun.security.util=ALL-UNNAMED"
: "${KASA_KEYSTORE:?set KASA_KEYSTORE to the .p12 signing key}"; : "${KASA_KEY_PASSWORD:?set KASA_KEY_PASSWORD}"
java $X -cp "$LIB/apksig-2.3.0.jar:build/signer" Sign build/unsigned.apk build/Kasa.apk "$KASA_KEY_PASSWORD" "$KASA_KEYSTORE"
java $X -cp "$LIB/apksig-2.3.0.jar:build/signer" Verify build/Kasa.apk
echo "Done: build/Kasa.apk"
