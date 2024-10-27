// Copyright (c) 2017-present, Rockset, Inc.  All rights reserved.
#include <cstdio>
#include <iostream>
#include <string>
#include <aws/core/Aws.h>
#include <aws/s3/S3Client.h>
#include <iostream>
#include <aws/core/auth/AWSCredentialsProviderChain.h>

#include "rocksdb/cloud/db_cloud.h"
#include "rocksdb/options.h"

using namespace ROCKSDB_NAMESPACE;

// This is the local directory where the db is stored.
std::string kDBPath = "/tmp/rocksdb_cloud_durable";

// This is the name of the cloud storage bucket where the db
// is made durable. if you are using AWS, you have to manually
// ensure that this bucket name is unique to you and does not
// conflict with any other S3 users who might have already created
// this bucket name.
std::string kBucketSuffix = "cloud.durable.example.";
std::string kRegion = "ap-northeast-2";

static const bool flushAtEnd = true;
static const bool disableWAL = false;

int main() {
      Aws::SDKOptions aws_options;
    // Optionally change the log level for debugging.
//   options.loggingOptions.logLevel = Utils::Logging::LogLevel::Debug;
    Aws::InitAPI(aws_options); // Should only be called once.
  // cloud environment config options here
  CloudFileSystemOptions cloud_fs_options;

  // Store a reference to a cloud file system. A new cloud env object should be
  // associated with every new cloud-db.
  std::shared_ptr<FileSystem> cloud_fs;

  // std::cout << getenv("AWS_ACCESS_KEY_ID") << " " << getenv("AWS_SECRET_ACCESS_KEY") << std::endl;

  // cloud_fs_options.credentials.InitializeSimple(
  //     getenv("AWS_ACCESS_KEY_ID"), getenv("AWS_SECRET_ACCESS_KEY"));
  // cloud_fs_options.credentials.InitializeConfig("/home/wjp/.aws/credentials");
  // if (!cloud_fs_options.credentials.HasValid().ok()) {
  //   fprintf(
  //       stderr,
  //       "Please set env variables "
  //       "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY with cloud credentials");
  //   return -1;
  // }

  std::cout << "init done" << std::endl;

  // Append the user name to the bucket name in an attempt to make it
  // globally unique. S3 bucket-names need to be globally unique.
  // If you want to rerun this example, then unique user-name suffix here.
  char* user = "wjp";
  kBucketSuffix.append(user);

  // "rockset." is the default bucket prefix
  const std::string bucketPrefix = "rockset.";
  cloud_fs_options.src_bucket.SetBucketName(kBucketSuffix, bucketPrefix);
  cloud_fs_options.dest_bucket.SetBucketName(kBucketSuffix, bucketPrefix);

  // create a bucket name for debugging purposes
  const std::string bucketName = bucketPrefix + kBucketSuffix;

  std::cout << "kBucketSuffix: " << kBucketSuffix << " kDBPath: " << kDBPath << " kRegion: " << kRegion << " bucketName: " << bucketName << std::endl;

  // Create a new AWS cloud env Status
  CloudFileSystem* cfs;
  Status s = CloudFileSystemEnv::NewAwsFileSystem(
      FileSystem::Default(), kBucketSuffix, kDBPath, kRegion, kBucketSuffix,
      kDBPath, kRegion, cloud_fs_options, nullptr, &cfs);
  if (!s.ok()) {
    fprintf(stderr, "Unable to create cloud env in bucket %s. %s\n",
            bucketName.c_str(), s.ToString().c_str());
    return -1;
  }
  cloud_fs.reset(cfs);

  // Create options and use the AWS file system that we created earlier
  auto cloud_env = NewCompositeEnv(cloud_fs);
  Options options;
  options.env = cloud_env.get();
  options.create_if_missing = true;
  options.compaction_style = rocksdb::kCompactionStyleLevel;
  options.write_buffer_size = 110 << 10;  // 110KB
  options.arena_block_size = 4 << 10;
  options.level0_file_num_compaction_trigger = 2;
  options.max_bytes_for_level_base = 100 << 10; // 100KB

  // No persistent read-cache
  std::string persistent_cache = "";

  // options for each write
  WriteOptions wopt;
  wopt.disableWAL = disableWAL;

  // open DB
  DBCloud* db;
  s = DBCloud::Open(options, kDBPath, persistent_cache, 0, &db);
  if (!s.ok()) {
    fprintf(stderr, "Unable to open db at path %s with bucket %s. %s\n",
            kDBPath.c_str(), bucketName.c_str(), s.ToString().c_str());
    return -1;
  }

  // Put key-value
  s = db->Put(wopt, "key1", "value");
  assert(s.ok());
  std::string value;
  // get value
  s = db->Get(ReadOptions(), "key1", &value);
  assert(s.ok());
  assert(value == "value");

  // atomically apply a set of updates
  {
    WriteBatch batch;
    batch.Delete("key1");
    batch.Put("key2", value);
    s = db->Write(wopt, &batch);
  }

  s = db->Get(ReadOptions(), "key1", &value);
  assert(s.IsNotFound());

  db->Get(ReadOptions(), "key2", &value);
  assert(value == "value");

  // for (int i = 0; i < 100000; i++) {
  //   WriteBatch batch;
  //   if (i % 1000 == 0) {
  //     printf("insert %d record\n", i);
  //   }
  //   batch.Put("mykey"+std::to_string(i), "val"+std::to_string(i));
  //   s = db->Write(wopt, &batch);
  // }

  s = db->Get(ReadOptions(), "mykey99998", &value);
  printf("get %s\n", value.c_str());

  // print all values in the database
  // ROCKSDB_NAMESPACE::Iterator* it =
  //     db->NewIterator(ROCKSDB_NAMESPACE::ReadOptions());
  // for (it->SeekToFirst(); it->Valid(); it->Next()) {
  //   std::cout << it->key().ToString() << ": " << it->value().ToString()
  //             << std::endl;
  // }
  // delete it;

  // Flush all data from main db to sst files. Release db.
  if (flushAtEnd) {
    db->Flush(FlushOptions());
  }
  delete db;

  fprintf(stdout, "Successfully used db at path %s in bucket %s.\n",
          kDBPath.c_str(), bucketName.c_str());
  
  Aws::ShutdownAPI(aws_options); // Should only be called once.
  return 0;
}
