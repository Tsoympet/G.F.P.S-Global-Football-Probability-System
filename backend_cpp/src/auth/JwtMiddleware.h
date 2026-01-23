#pragma once

#include <drogon/HttpFilter.h>
#include <drogon/plugins/Jwt.h>
#include <string>

namespace auth {
class JwtMiddleware : public drogon::HttpFilter<JwtMiddleware> {
  public:
    JwtMiddleware() = default;
    void doFilter(const drogon::HttpRequestPtr& req, FilterCallback&& cb, FilterChainCallback&& forward) override;
};
}  // namespace auth
