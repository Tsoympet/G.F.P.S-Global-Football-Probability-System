#pragma once

#include <drogon/HttpController.h>
#include <memory>

namespace auth { class JwtMiddleware; }
namespace services { class ProbabilityEngine; class ConfidenceEngine; }

namespace controllers {
class PredictionsController : public drogon::HttpController<PredictionsController> {
  public:
    PredictionsController() = default;

    METHOD_LIST_BEGIN
    ADD_METHOD_TO(PredictionsController::predict, "/predict", drogon::Post, "auth::JwtMiddleware");
    METHOD_LIST_END

    void predict(const drogon::HttpRequestPtr& req, std::function<void(const drogon::HttpResponsePtr&)>&& cb) const;
};
}  // namespace controllers
