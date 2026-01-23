#include "ValueController.h"

#include <drogon/HttpResponse.h>
#include <nlohmann/json.hpp>

#include "services/EVEngine.h"
#include "utils/JsonUtils.h"

namespace controllers {

ValueController::ValueController(std::shared_ptr<auth::JwtMiddleware> auth)
    : auth_(std::move(auth)) {}

void ValueController::value(const drogon::HttpRequestPtr& req, std::function<void(const drogon::HttpResponsePtr&)>&& cb) const {
    nlohmann::json json;
    try {
        json = utils::JsonUtils::parse(req);
    } catch (const std::exception& ex) {
        auto resp = drogon::HttpResponse::newHttpResponse();
        resp->setStatusCode(drogon::k400BadRequest);
        resp->setBody(ex.what());
        cb(resp);
        return;
    }
    const double probability = json.value("probability", 0.0);
    const double odds = json.value("odds", 1.0);

    services::EVEngine ev;
    const auto evValue = ev.expectedValue(probability, odds);

    nlohmann::json respJson{{"expected_value", evValue}};
    auto resp = drogon::HttpResponse::newHttpJsonResponse(respJson);
    resp->setStatusCode(drogon::k200OK);
    cb(resp);
}

}  // namespace controllers
