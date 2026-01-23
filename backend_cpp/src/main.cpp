#include <drogon/drogon.h>
#include <filesystem>
#include "App.h"

int main(int argc, char** argv) {
    try {
        gfps::App app;
        std::string configPath = "config/config.json";
        if (!std::filesystem::exists(configPath)) {
            configPath = "../config/config.json";
        }
        app.configure(configPath);
        app.run();
    } catch (const std::exception& ex) {
        std::cerr << "Failed to start application: " << ex.what() << std::endl;
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
