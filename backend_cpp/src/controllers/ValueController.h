#pragma once

#include <drogon/HttpController.h>
#include <memory>

namespace auth { class JwtMiddleware; }
namespace services { class EVEngine; }

namespace controllers {
class ValueController : public drogon::HttpController<ValueController> {
  public:
    ValueController() = default;

    METHOD_LIST_BEGIN
    ADD_METHOD_TO(ValueController::value, "/value", drogon::Post, "auth::JwtMiddleware");
    METHOD_LIST_END

    void value(const drogon::HttpRequestPtr& req, std::function<void(const drogon::HttpResponsePtr&)>&& cb) const;
};
}  // namespace controllers
