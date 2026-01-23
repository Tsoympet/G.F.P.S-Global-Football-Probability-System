#include "HealthController.h"

#include <drogon/HttpResponse.h>
#include <nlohmann/json.hpp>

namespace controllers {

void HealthController::health(const drogon::HttpRequestPtr&, std::function<void(const drogon::HttpResponsePtr&)>&& callback) const {
    nlohmann::json payload{{"status", "ok"}, {"backend", "cpp"}};
    auto resp = drogon::HttpResponse::newHttpJsonResponse(payload);
    resp->setStatusCode(drogon::k200OK);
    callback(resp);
}

}  // namespace controllers
