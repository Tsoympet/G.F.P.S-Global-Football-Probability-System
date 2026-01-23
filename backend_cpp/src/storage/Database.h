#pragma once

#include <sqlite_modern_cpp.h>
#include <string>
#include <mutex>

namespace storage {
class Database {
  public:
    static Database& instance();
    void connect(const std::string& path);
    sqlite::database& db();

  private:
    Database() = default;
    std::mutex mutex_;
    std::unique_ptr<sqlite::database> db_;
};
}  // namespace storage
