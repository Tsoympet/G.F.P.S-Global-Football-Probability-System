#include "AuthController.h"

#include <drogon/HttpResponse.h>
#include <drogon/plugins/Jwt.h>
#include <nlohmann/json.hpp>

#include "utils/JsonUtils.h"
#include "utils/TimeUtils.h"

namespace controllers {

AuthController::AuthController(std::string secret, int expiryMinutes)
    : secret_(std::move(secret)), expiryMinutes_(expiryMinutes) {}

void AuthController::login(const drogon::HttpRequestPtr& req, std::function<void(const drogon::HttpResponsePtr&)>&& callback) const {
    nlohmann::json json;
    try {
        json = utils::JsonUtils::parse(req);
    } catch (const std::exception& ex) {
        auto resp = drogon::HttpResponse::newHttpResponse();
        resp->setStatusCode(drogon::k400BadRequest);
        resp->setBody(ex.what());
        callback(resp);
        return;
    }

    const auto username = json.value("username", "");
    const auto password = json.value("password", "");

    // In production, validate against persistent store
    if (username.empty() || password.empty()) {
        auto resp = drogon::HttpResponse::newHttpResponse();
        resp->setStatusCode(drogon::k400BadRequest);
        resp->setBody("Missing credentials");
        callback(resp);
        return;
    }

    nlohmann::json claims;
    claims["sub"] = username;
    auto expiry = trantor::Date::date().after(expiryMinutes_ * 60);
    claims["exp"] = utils::TimeUtils::toUnix(expiry);

    auto token = drogon::plugins::Jwt::token(claims, secret_, drogon::plugins::Jwt::alg::HS256);

    nlohmann::json payload{{"access_token", token}, {"token_type", "bearer"}};
    auto resp = drogon::HttpResponse::newHttpJsonResponse(payload);
    resp->setStatusCode(drogon::k200OK);
    callback(resp);
}

}  // namespace controllers
