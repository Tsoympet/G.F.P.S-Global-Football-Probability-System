#pragma once

#include <drogon/HttpController.h>

namespace controllers {
class FixturesController : public drogon::HttpController<FixturesController> {
  public:
    METHOD_LIST_BEGIN
    ADD_METHOD_TO(FixturesController::listFixtures, "/fixtures", drogon::Get, "auth::JwtMiddleware");
    METHOD_LIST_END

    void listFixtures(const drogon::HttpRequestPtr& req, std::function<void(const drogon::HttpResponsePtr&)>&& cb) const;
};
}  // namespace controllers
