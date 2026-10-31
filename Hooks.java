// SPDX-License-Identifier: LGPL-3.0-or-later
package local.surface.density;

import android.app.Application;
import android.app.Instrumentation;
import android.content.Context;
import android.content.res.Configuration;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.WindowManager;
import java.lang.reflect.*;
import java.util.ArrayList;
import java.util.Arrays;

public final class Hooks {
    static final String TAG = "SQ2DensityTest";
    static final ArrayList<Hooks> live = new ArrayList<>();
    static Context context;
    static boolean installed;
    static int reports;
    static Class<?> densityClass;
    Method backup;
    Member target;
    String kind;
    static native Method hook(Member target, Object owner, Method callback);
    static native boolean unhook(Member target);
    static native boolean deopt(Member target);

    public static final class Subject { public static int value() { return 7; } }

    static Hooks add(Member target, String kind) throws Exception {
        Hooks h = new Hooks(); h.target = target; h.kind = kind;
        ((AccessibleObject) target).setAccessible(true);
        h.backup = hook(target, h, Hooks.class.getDeclaredMethod("callback", Object[].class));
        if (h.backup == null) throw new IllegalStateException("Hook failed: " + target);
        h.backup.setAccessible(true); live.add(h); return h;
    }
    Object original(Object[] args) throws Throwable {
        boolean stat = Modifier.isStatic(target.getModifiers());
        try { return backup.invoke(stat ? null : args[0], stat ? args : Arrays.copyOfRange(args, 1, args.length)); }
        catch (InvocationTargetException e) { throw e.getCause(); }
    }
    public Object callback(Object[] args) throws Throwable {
        if (kind.equals("subject")) return 11;
        if (kind.equals("newApplication")) {
            Log.i(TAG, "INSTALL_STAGE newApplication class=" + args[2]);
            install((Context) args[3]);
            return original(args);
        }
        if (kind.equals("attach")) {
            Log.i(TAG, "INSTALL_STAGE attach");
            install((Context) args[1]);
            return original(args);
        }
        if (kind.equals("onCreate")) {
            Log.i(TAG, "INSTALL_STAGE onCreate");
            install((Application) args[1]);
            return original(args);
        }
        if (kind.equals("construct")) {
            Object result = original(args);
            synchronizeCaches();
            return result;
        }
        if (kind.equals("metrics")) {
            DisplayMetrics prior = (DisplayMetrics) original(args);
            DisplayMetrics actual = windowMetrics();
            if (prior == null || actual == null) return prior;
            DisplayMetrics out = new DisplayMetrics(); out.setTo(prior);
            out.densityDpi = actual.densityDpi; out.density = actual.density;
            out.scaledDensity = actual.scaledDensity;
            if (reports++ < 6) Log.i(TAG, "metrics " + prior.densityDpi + " -> " + out.densityDpi
                    + " pixels=" + out.widthPixels + "x" + out.heightPixels);
            return out;
        }
        return original(args);
    }
    static DisplayMetrics windowMetrics() {
        try {
            DisplayMetrics dm = new DisplayMetrics();
            ((WindowManager) context.getSystemService(Context.WINDOW_SERVICE)).getDefaultDisplay().getMetrics(dm);
            return dm.densityDpi > 0 ? dm : null;
        } catch (Throwable t) { Log.e(TAG, "window metrics unavailable", t); return null; }
    }
    static void densityFields(DisplayMetrics dm, DisplayMetrics actual) {
        dm.densityDpi = actual.densityDpi;
        dm.density = actual.density;
        dm.scaledDensity = actual.scaledDensity;
    }
    static synchronized void synchronizeCaches() {
        try {
            DisplayMetrics actual = windowMetrics();
            if (actual == null) return;
            int updated = 0;
            for (Field f : densityClass.getDeclaredFields()) {
                if (Modifier.isStatic(f.getModifiers()) && f.getType() == DisplayMetrics.class) {
                    f.setAccessible(true);
                    DisplayMetrics cached = (DisplayMetrics) f.get(null);
                    if (cached != null) { densityFields(cached, actual); updated++; }
                }
            }
            // The constructor also copies the cached metrics directly into theme resources.
            densityFields(context.getResources().getDisplayMetrics(), actual);
            densityFields(context.getTheme().getResources().getDisplayMetrics(), actual);
            Log.i(TAG, "CACHES_SYNCHRONIZED count=" + updated + " dpi=" + actual.densityDpi);
        } catch (Throwable t) { Log.e(TAG, "CACHE_SYNC_FAILED", t); }
    }
    static synchronized void install(Context c) {
        if (installed || !"com.tencent.mm".equals(c.getPackageName())) return;
        int before = live.size();
        try {
            if (c.getPackageManager().getPackageInfo("com.tencent.mm", 0).getLongVersionCode() != 3200L)
                throw new IllegalStateException("Only verified WeChat 8.0.79/versionCode 3200 is supported");
            context = c.getApplicationContext() != null ? c.getApplicationContext() : c;
            Class<?> density = Class.forName("jf5.f", false, c.getClassLoader());
            densityClass = density;
            Method raw = density.getDeclaredMethod("d");
            Method adjusted = density.getDeclaredMethod("e");
            if (!Modifier.isStatic(raw.getModifiers()) || Modifier.isStatic(adjusted.getModifiers())
                    || raw.getReturnType() != DisplayMetrics.class || adjusted.getReturnType() != DisplayMetrics.class)
                throw new IllegalStateException("Density method shape changed");
            DisplayMetrics dm = windowMetrics();
            if (dm == null) throw new IllegalStateException("Window density unavailable");
            // Keep h() and the Bitmap/default-density synchronization in i() active.
            // Disabling h() makes text/resources and decoded bitmaps disagree.
            add(raw, "metrics"); add(adjusted, "metrics");
            for (Constructor<?> ctor : density.getDeclaredConstructors()) add(ctor, "construct");
            // Avoid compiled callers retaining an inlined d()/e() implementation.
            for (Constructor<?> ctor : density.getDeclaredConstructors()) deopt(ctor);
            for (Method method : density.getDeclaredMethods()) deopt(method);
            installed = true;
            Log.i(TAG, "WECHAT_HOOKS_READY variant=pre-application-cache-sync windowDpi=" + dm.densityDpi + " model=" + android.os.Build.MODEL
                    + " brand=" + android.os.Build.BRAND + " class=" + density.getName());
        } catch (Throwable t) {
            for (int i = live.size() - 1; i >= before; --i) {
                Hooks h = live.remove(i); unhook(h.target);
            }
            Log.e(TAG, "WECHAT_HOOKS_NOT_INSTALLED", t);
        }
    }
    public static void start(String mode) {
        try {
            if (mode.equals("probe")) {
                Method method = Subject.class.getDeclaredMethod("value");
                int before = (Integer) method.invoke(null);
                Hooks h = add(method, "subject");
                int after = (Integer) method.invoke(null);
                int backup = (Integer) h.backup.invoke(null);
                boolean removed = unhook(method);
                int restored = (Integer) method.invoke(null);
                if (before != 7 || after != 11 || backup != 7 || !removed || restored != 7)
                    throw new IllegalStateException("Probe mismatch " + before + "/" + after + "/" + backup + "/" + restored);
                Log.i(TAG, "PROBE_PASS before=7 hooked=11 backup=7 restored=7 model=" + android.os.Build.MODEL);
                return;
            }
            add(Instrumentation.class.getDeclaredMethod("newApplication", ClassLoader.class, String.class, Context.class), "newApplication");
            add(Application.class.getDeclaredMethod("attach", Context.class), "attach");
            add(Instrumentation.class.getDeclaredMethod("callApplicationOnCreate", Application.class), "onCreate");
            Log.i(TAG, "APPLICATION_HOOKS_READY");
        } catch (Throwable t) { Log.e(TAG, "BOOTSTRAP_FAILED", t); }
    }
}
