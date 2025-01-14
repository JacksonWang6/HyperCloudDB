Rocksmash核心设计就是元数据压缩，快速云存储缓存所有元数据以及在快速云存储当中缓存慢速云存储中的热数据块
这里采用简单的二级缓存实现，使用Cachelib作为二级缓存

安装的2023年的Cachelib的stable版本，Cachelib库的gtest换个名字，不然会和本仓库的gtest冲突
主要修改就是使用Cachelib实现了二级缓存以及让其通过编译。

https://seekstar.github.io/2023/11/22/cachelib%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0/

