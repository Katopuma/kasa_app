package app.kasa;

import android.app.Activity;
import android.content.Intent;
import android.content.res.Configuration;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class MainActivity extends Activity {
    private WebView web;
    private static final String[][] RATE_SOURCES = {
        {"https://open.er-api.com/v6/latest/EUR", "open.er-api.com"},
        {"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json", "currency-api"},
        {"https://latest.currency-api.pages.dev/v1/currencies/eur.json", "currency-api"}
    };

    private boolean night() {
        return (getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES;
    }

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        boolean n = night();
        int bg = n ? 0xff0d1230 : 0xfff2effa;
        applyBars(n ? 0xff0d1230 : 0xfff2effa, n ? 0xff161c42 : 0xffffffff, !n);
        web = new WebView(this);
        web.setBackgroundColor(bg);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(false);
        s.setGeolocationEnabled(false);
        s.setSaveFormData(false);
        web.addJavascriptInterface(new Bridge(), "KasaNative");
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, String url) {
                if (url.startsWith("file:///android_asset/")) return false;
                try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); } catch (Exception e) { }
                return true;
            }
        });
        setContentView(web);
        web.loadUrl("file:///android_asset/index.html");
    }

    @Override
    public void onConfigurationChanged(Configuration c) {
        super.onConfigurationChanged(c);
        if (web != null) web.loadUrl("javascript:window.onNativeNight&&onNativeNight(" + night() + ")");
    }

    @Override
    public void onBackPressed() {
        if (web != null) web.loadUrl("javascript:window.kasaBack?kasaBack():KasaNative.exit()");
        else super.onBackPressed();
    }

    private void applyBars(int status, int nav, boolean lightIcons) {
        Window w = getWindow();
        try {
            w.getClass().getMethod("setStatusBarColor", int.class).invoke(w, status);
            w.getClass().getMethod("setNavigationBarColor", int.class).invoke(w, nav);
        } catch (Exception e) { }
        View d = w.getDecorView();
        int flags = 0;
        if (lightIcons) flags |= 0x00002000 | 0x00000010; // light status bar + light navigation bar
        d.setSystemUiVisibility(flags);
    }

    private File dataFile() { return new File(getFilesDir(), "kasa.json"); }

    private static int parseColor(String c, int def) {
        try { return Color.parseColor(c); } catch (Exception e) { return def; }
    }

    class Bridge {
        @JavascriptInterface
        public boolean isNight() { return night(); }

        @JavascriptInterface
        public String load() {
            File f = dataFile();
            if (!f.exists()) return null;
            try {
                FileInputStream in = new FileInputStream(f);
                ByteArrayOutputStream out = new ByteArrayOutputStream();
                byte[] buf = new byte[8192]; int r;
                while ((r = in.read(buf)) > 0) out.write(buf, 0, r);
                in.close();
                return out.toString("UTF-8");
            } catch (Exception e) { return null; }
        }

        @JavascriptInterface
        public synchronized boolean save(String json) {
            File tmp = new File(getFilesDir(), "kasa.json.tmp");
            try {
                FileOutputStream out = new FileOutputStream(tmp);
                out.write(json.getBytes("UTF-8"));
                out.getFD().sync();
                out.close();
                return tmp.renameTo(dataFile());
            } catch (Exception e) { return false; }
        }

        @JavascriptInterface
        public void setBars(final String status, final String bg, final boolean light) {
            runOnUiThread(new Runnable() { public void run() {
                int nav = parseColor(status, 0xffffffff);
                int st = parseColor(bg, 0xfff2effa);
                applyBars(st, nav, light);
                if (web != null) web.setBackgroundColor(st);
            }});
        }

        @JavascriptInterface
        public void share(final String text) {
            runOnUiThread(new Runnable() { public void run() {
                Intent i = new Intent(Intent.ACTION_SEND);
                i.setType("text/plain");
                i.putExtra(Intent.EXTRA_SUBJECT, "Каса: резервная копия");
                i.putExtra(Intent.EXTRA_TEXT, text);
                try { startActivity(Intent.createChooser(i, "Сохранить копию")); } catch (Exception e) { }
            }});
        }

        @JavascriptInterface
        public void exit() {
            runOnUiThread(new Runnable() { public void run() { finish(); } });
        }

        @JavascriptInterface
        public void fetchRates() {
            new Thread(new Runnable() { public void run() {
                for (String[] src : RATE_SOURCES) {
                    String body = get(src[0]);
                    if (body != null) {
                        final String js = "javascript:window.onNativeRates&&onNativeRates(" + q(body) + "," + q(src[1]) + ")";
                        runOnUiThread(new Runnable() { public void run() { if (web != null) web.loadUrl(js); } });
                        return;
                    }
                }
            }}).start();
        }
    }

    private static String q(String s) {
        StringBuilder b = new StringBuilder("\"");
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch == '"' || ch == '\\') { b.append('\\').append(ch); }
            else if (ch < 0x20 || ch == 0x2028 || ch == 0x2029 || ch == '<' || ch == '>' || ch == '%') { b.append(String.format("\\u%04x", (int) ch)); }
            else b.append(ch);
        }
        return b.append('"').toString();
    }

    private static String get(String u) {
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(u).openConnection();
            c.setConnectTimeout(8000);
            c.setReadTimeout(8000);
            c.setRequestProperty("Accept", "application/json");
            if (c.getResponseCode() != 200) return null;
            InputStream in = c.getInputStream();
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[8192]; int r;
            while ((r = in.read(buf)) > 0) { out.write(buf, 0, r); if (out.size() > 2000000) return null; }
            in.close();
            return out.toString("UTF-8");
        } catch (Exception e) {
            return null;
        } finally {
            if (c != null) c.disconnect();
        }
    }
}
