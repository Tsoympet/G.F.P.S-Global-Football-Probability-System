#include "JsonUtils.h"

#include <stdexcept>

namespace utils {

nlohmann::json JsonUtils::parse(const drogon::HttpRequestPtr& req) {
    try {
        if (req->getBody().empty()) {
            return nlohmann::json::object();
        }
        return nlohmann::json::parse(req->getBody());
    } catch (const std::exception& ex) {
        throw std::runtime_error(std::string{"Invalid JSON: "} + ex.what());
    }
}

}  // namespace utils
