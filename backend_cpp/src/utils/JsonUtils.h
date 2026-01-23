#pragma once

#include <drogon/HttpRequest.h>
#include <nlohmann/json.hpp>

namespace utils {
class JsonUtils {
  public:
    static nlohmann::json parse(const drogon::HttpRequestPtr& req);
};
}  // namespace utils
