#pragma once

namespace services {
class EVEngine {
  public:
    double expectedValue(double probability, double odds) const;
};
}  // namespace services
