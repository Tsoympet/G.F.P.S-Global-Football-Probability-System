#include "PredictionsController.h"

#include <drogon/HttpResponse.h>
#include <nlohmann/json.hpp>

#include "services/ConfidenceEngine.h"
#include "services/ProbabilityEngine.h"
#include "utils/JsonUtils.h"

namespace controllers {

void PredictionsController::predict(const drogon::HttpRequestPtr& req, std::function<void(const drogon::HttpResponsePtr&)>&& cb) const {
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
    const auto homeGoals = json.value("home_goals", 1.2);
    const auto awayGoals = json.value("away_goals", 1.0);

    services::ProbabilityEngine prob;
    const auto resultProbs = prob.compute1X2(homeGoals, awayGoals);
    services::ConfidenceEngine confidence;
    auto confidenceScore = confidence.score(resultProbs);

    nlohmann::json respJson{{"home_win", resultProbs.homeWin}, {"draw", resultProbs.draw}, {"away_win", resultProbs.awayWin}, {"confidence", confidenceScore}};
    auto resp = drogon::HttpResponse::newHttpJsonResponse(respJson);
    resp->setStatusCode(drogon::k200OK);
    cb(resp);
}

}  // namespace controllers
