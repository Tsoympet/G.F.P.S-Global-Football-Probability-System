#pragma once

#include <string>

namespace models {
struct Team {
    int id{};
    std::string name;
    double attackStrength{};
    double defenseStrength{};
};
}
