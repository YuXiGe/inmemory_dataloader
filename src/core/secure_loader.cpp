#include <vector>
#include <fstream>
#include <algorithm>
#include <iostream>
#include <sys/mman.h>
#include <cstring>
#include <cmath>

extern "C" {
    // 内部演算用プロトタイプを先に宣言
    float multi_pass_wave(float val, float sigma) {
        return (val > 0) ? std::sin(val * sigma) : 0.0f; 
    }

    /**
     * @brief 完全インメモリ演算（証跡抹消・スワップ防止機能付き）
     */
    void secure_compute_cpu(const char* filename, float* out, float sigma, unsigned char key) {
        std::ifstream file(filename, std::ios::binary | std::ios::ate);
        if (!file.is_open()) return;

        std::streamsize size = file.tellg();
        file.seekg(0, std::ios::beg);

        // 1. RAM確保とスワップ防止 (mlock)
        std::vector<unsigned char> ram_buffer(size);
        if (mlock(ram_buffer.data(), size) != 0) {
            std::cerr << "⚠️ [Security Warning] Could not lock memory. Swap may occur." << std::endl;
        }

        if (!file.read(reinterpret_cast<char*>(ram_buffer.data()), size)) {
            munlock(ram_buffer.data(), size);
            return;
        }
        file.close();

        // 2. メモリ上でのみ復号（オン・ザ・フライ）
        for (size_t i = 0; i < ram_buffer.size(); ++i) {
            ram_buffer[i] ^= key;
        }

        // 3. 演算実行
        const float* raw_data = reinterpret_cast<const float*>(ram_buffer.data());
        size_t n = size / sizeof(float);
        for (size_t i = 0; i < n; ++i) {
            out[i] = multi_pass_wave(raw_data[i], sigma);
        }

        // 4. 【重要】証跡抹消
        volatile unsigned char* p = static_cast<volatile unsigned char*>(ram_buffer.data());
        std::fill(p, p + size, 0);
        
        munlock(ram_buffer.data(), size);
        printf("🔐 [Security] Computation finished. Raw data wiped from RAM.\n");
    }
}
