#pragma once

#include <trantor/utils/Date.h>

namespace utils {
class TimeUtils {
  public:
    static int64_t toUnix(const trantor::Date& date);
};
}  // namespace utils
