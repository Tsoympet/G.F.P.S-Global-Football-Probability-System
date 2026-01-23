#include "App.h"

#include <drogon/drogon.h>
#include <drogon/plugins/Jwt.h>
#include <nlohmann/json.hpp>
#include <fstream>
#include <stdexcept>

#include "auth/JwtMiddleware.h"
#include "controllers/AuthController.h"
#include "controllers/FixturesController.h"
#include "controllers/HealthController.h"
#include "controllers/PredictionsController.h"
#include "controllers/ValueController.h"
#include "services/ConfidenceEngine.h"
#include "services/EVEngine.h"
#include "services/ProbabilityEngine.h"
#include "storage/Database.h"
#include "utils/JsonUtils.h"
#include "utils/TimeUtils.h"

namespace gfps {

void App::configure(const std::string& configPath) {
    std::ifstream file(configPath);
    if (!file.is_open()) {
        throw std::runtime_error("Unable to open config file: " + configPath);
    }
    auto config = nlohmann::json::parse(file);

    jwtSecret_ = config.value("jwt_secret", "change_me");
    expiryMinutes_ = config.value("jwt_expiry_minutes", 60);

    drogon::app().loadConfigFile(configPath);

    auto dbPath = config.value("database_path", std::string{"data/gfps.db"});
    auto& db = storage::Database::instance();
    db.connect(dbPath);

    setupRoutes();
}

void App::setupRoutes() {
    auto& app = drogon::app();
    app.registerController(std::make_shared<controllers::HealthController>());

    drogon::app().registerFilter(std::make_shared<auth::JwtMiddleware>());
    app.registerController(std::make_shared<controllers::AuthController>(jwtSecret_, expiryMinutes_));
    app.registerController(std::make_shared<controllers::FixturesController>());
    app.registerController(std::make_shared<controllers::PredictionsController>());
    app.registerController(std::make_shared<controllers::ValueController>());
}

void App::run() {
    drogon::app().run();
}

}  // namespace gfps
