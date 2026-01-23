#pragma once

#include <string>
#include <drogon/drogon.h>

namespace gfps {
class App {
  public:
    void configure(const std::string& configPath);
    void run();
  private:
    void setupRoutes();
    std::string jwtSecret_;
    int expiryMinutes_{60};
};
}  // namespace gfps
