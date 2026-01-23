#include "JwtMiddleware.h"

#include <drogon/HttpResponse.h>
#include <drogon/plugins/Jwt.h>
#include <drogon/drogon.h>

namespace auth {

void JwtMiddleware::doFilter(const drogon::HttpRequestPtr& req, FilterCallback&& cb, FilterChainCallback&& forward) {
    const auto authHeader = req->getHeader("Authorization");
    if (authHeader.rfind("Bearer ", 0) != 0) {
        auto resp = drogon::HttpResponse::newHttpResponse();
        resp->setStatusCode(drogon::k401Unauthorized);
        resp->setBody("Missing token");
        cb(resp);
        return;
    }
    const auto token = authHeader.substr(7);

    try {
        auto secret = drogon::app().getCustomConfig()["jwt_secret"].as<std::string>();
        drogon::plugins::Jwt::verify(token, secret, drogon::plugins::Jwt::alg::HS256);
        forward();
    } catch (...) {
        auto resp = drogon::HttpResponse::newHttpResponse();
        resp->setStatusCode(drogon::k401Unauthorized);
        resp->setBody("Invalid token");
        cb(resp);
    }
}

}  // namespace auth
