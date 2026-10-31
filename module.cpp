// SPDX-License-Identifier: LGPL-3.0-or-later
#include <android/log.h>
#include <fcntl.h>
#include <time.h>
#include <unistd.h>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include "zygisk.hpp"
#include "lsplant.hpp"
#include "dobby.h"
#include "xdl.h"

#define LOG(...) __android_log_print(ANDROID_LOG_INFO, "SQ2DensityTest", __VA_ARGS__)
static void *art_handle;
static std::vector<unsigned char> payload;

static jobject hook(JNIEnv *env, jclass, jobject target, jobject owner, jobject callback) {
    return lsplant::Hook(env, target, owner, callback);
}
static jboolean unhook(JNIEnv *env, jclass, jobject target) {
    return lsplant::UnHook(env, target);
}
static jboolean deopt(JNIEnv *env, jclass, jobject target) {
    return lsplant::Deoptimize(env, target);
}
static bool exception(JNIEnv *env, const char *stage) {
    if (!env->ExceptionCheck()) return false;
    LOG("JNI failure at %s", stage);
    env->ExceptionDescribe();
    env->ExceptionClear();
    return true;
}

class DensityModule final : public zygisk::ModuleBase {
    zygisk::Api *api = nullptr;
    JNIEnv *env = nullptr;
    std::string mode;
    bool target = false;
public:
    void onLoad(zygisk::Api *a, JNIEnv *e) override { api = a; env = e; }
    void preServerSpecialize(zygisk::ServerSpecializeArgs *) override {
        api->setOption(zygisk::DLCLOSE_MODULE_LIBRARY);
    }
    void preAppSpecialize(zygisk::AppSpecializeArgs *args) override {
        target = false;
        const char *name = env->GetStringUTFChars(args->nice_name, nullptr);
        std::string process(name);
        env->ReleaseStringUTFChars(args->nice_name, name);
        // Main process only, and only Android user 10 in this lab test.
        if (args->uid / 100000 != 10 ||
            (process != "com.tencent.mm" && process != "local.surface.identityprobe")) {
            api->setOption(zygisk::DLCLOSE_MODULE_LIBRARY);
            return;
        }
        char boot[80] = {}, expected[80] = {}, selected[20] = {};
        long deadline = 0;
        FILE *f = fopen("/proc/sys/kernel/random/boot_id", "r");
        if (f) { fscanf(f, "%79s", boot); fclose(f); }
        f = fopen("/data/adb/sq2-density-test/gate", "r");
        if (f) { fscanf(f, "%79s %ld %19s", expected, &deadline, selected); fclose(f); }
        timespec now{}; clock_gettime(CLOCK_BOOTTIME, &now);
        mode = selected;
        if (!boot[0] || strcmp(boot, expected) || now.tv_sec > deadline ||
            !((mode == "probe" && process == "local.surface.identityprobe") ||
              (mode == "wechat" && process == "com.tencent.mm"))) {
            api->setOption(zygisk::DLCLOSE_MODULE_LIBRARY);
            return;
        }
        int dir = api->getModuleDir();
        int fd = dir < 0 ? -1 : openat(dir, "classes.dex", O_RDONLY | O_CLOEXEC);
        if (dir >= 0) close(dir);
        if (fd < 0) { LOG("payload unavailable"); api->setOption(zygisk::DLCLOSE_MODULE_LIBRARY); return; }
        off_t size = lseek(fd, 0, SEEK_END);
        if (size <= 0 || size > 1024 * 1024 || lseek(fd, 0, SEEK_SET) < 0) {
            close(fd); api->setOption(zygisk::DLCLOSE_MODULE_LIBRARY); return;
        }
        payload.resize(size);
        size_t done = 0;
        while (done < payload.size()) {
            ssize_t n = read(fd, payload.data() + done, payload.size() - done);
            if (n <= 0) break;
            done += n;
        }
        close(fd);
        target = done == payload.size();
        if (!target) api->setOption(zygisk::DLCLOSE_MODULE_LIBRARY);
    }
    void postAppSpecialize(const zygisk::AppSpecializeArgs *) override {
        if (!target) return;
        LOG("target process pid=%d mode=%s", getpid(), mode.c_str());
        art_handle = xdl_open("libart.so", XDL_DEFAULT);
        if (!art_handle) { LOG("libart unavailable"); return; }
        lsplant::InitInfo info{
            .inline_hooker = [](void *address, void *replacement) -> void * {
                void *backup = nullptr;
                return DobbyHook(address, replacement, &backup) == 0 ? backup : nullptr;
            },
            .inline_unhooker = [](void *address) { return DobbyDestroy(address) == 0; },
            .art_symbol_resolver = [](std::string_view name) -> void * {
                std::string s(name);
                void *p = xdl_sym(art_handle, s.c_str(), nullptr);
                return p ? p : xdl_dsym(art_handle, s.c_str(), nullptr);
            },
            .art_symbol_prefix_resolver = [](std::string_view) -> void * { return nullptr; },
        };
        if (!lsplant::Init(env, info)) { LOG("LSPLANT_INIT_FAILED"); exception(env, "Init"); return; }
        LOG("LSPLANT_INIT_OK");
        jclass cl = env->FindClass("java/lang/ClassLoader");
        jmethodID system = env->GetStaticMethodID(cl, "getSystemClassLoader", "()Ljava/lang/ClassLoader;");
        jobject parent = env->CallStaticObjectMethod(cl, system);
        jclass im = env->FindClass("dalvik/system/InMemoryDexClassLoader");
        jmethodID ctor = env->GetMethodID(im, "<init>", "(Ljava/nio/ByteBuffer;Ljava/lang/ClassLoader;)V");
        jobject bytes = env->NewDirectByteBuffer(payload.data(), payload.size());
        jobject loader = env->NewObject(im, ctor, bytes, parent);
        if (exception(env, "DexClassLoader") || !loader) return;
        jmethodID load = env->GetMethodID(cl, "loadClass", "(Ljava/lang/String;)Ljava/lang/Class;");
        auto entry = (jclass) env->CallObjectMethod(loader, load, env->NewStringUTF("local.surface.density.Hooks"));
        if (exception(env, "load Hooks") || !entry) return;
        JNINativeMethod methods[] = {
            {const_cast<char *>("hook"), const_cast<char *>("(Ljava/lang/reflect/Member;Ljava/lang/Object;Ljava/lang/reflect/Method;)Ljava/lang/reflect/Method;"), (void *) hook},
            {const_cast<char *>("unhook"), const_cast<char *>("(Ljava/lang/reflect/Member;)Z"), (void *) unhook},
            {const_cast<char *>("deopt"), const_cast<char *>("(Ljava/lang/reflect/Member;)Z"), (void *) deopt},
        };
        if (env->RegisterNatives(entry, methods, 3) != 0 || exception(env, "RegisterNatives")) return;
        jmethodID start = env->GetStaticMethodID(entry, "start", "(Ljava/lang/String;)V");
        env->CallStaticVoidMethod(entry, start, env->NewStringUTF(mode.c_str()));
        exception(env, "start");
    }
};
REGISTER_ZYGISK_MODULE(DensityModule)
