#pragma once

#include <drogon/HttpController.h>
#include <string>

namespace controllers {
class AuthController : public drogon::HttpController<AuthController> {
  public:
    explicit AuthController(std::string secret, int expiryMinutes);

    METHOD_LIST_BEGIN
    ADD_METHOD_TO(AuthController::login, "/auth/login", drogon::Post);
    METHOD_LIST_END

    void login(const drogon::HttpRequestPtr& req, std::function<void(const drogon::HttpResponsePtr&)>&& callback) const;

  private:
    std::string secret_;
    int expiryMinutes_;
};
}  // namespace controllers
