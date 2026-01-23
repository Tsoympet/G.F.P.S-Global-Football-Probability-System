#include "FixturesController.h"

#include <drogon/HttpResponse.h>
#include <nlohmann/json.hpp>

namespace controllers {

void FixturesController::listFixtures(const drogon::HttpRequestPtr&, std::function<void(const drogon::HttpResponsePtr&)>&& cb) const {
    nlohmann::json fixtures = {
        {{"home_team", "Team A"}, {"away_team", "Team B"}, {"kickoff", "2024-01-01T12:00:00Z"}},
        {{"home_team", "Team C"}, {"away_team", "Team D"}, {"kickoff", "2024-01-02T12:00:00Z"}}
    };
    auto resp = drogon::HttpResponse::newHttpJsonResponse(fixtures);
    resp->setStatusCode(drogon::k200OK);
    cb(resp);
}

}  // namespace controllers
