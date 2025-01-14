# See the License for the specific language governing permissions and
# limitations under the License.
# pull the newest version of gtest

git submodule sync

git submodule init

git submodule update

set -e

# Root directory for the CacheLib project
CLBASE="/home/wjp/CacheLib"

# Additional "FindXXX.cmake" files are here (e.g. FindSodium.cmake)
CLCMAKE="$CLBASE/cachelib/cmake"

# After ensuring we are in the correct directory, set the installation prefix"
PREFIX="$CLBASE/opt/cachelib/"

CMAKE_PARAMS="-DCMAKE_INSTALL_PREFIX='$PREFIX' -DCMAKE_MODULE_PATH='$CLCMAKE'"

CMAKE_PREFIX_PATH="${CMAKE_PREFIX_PATH:-}:$PREFIX/lib/cmake:$PREFIX/lib64/cmake"
# CMAKE_PREFIX_PATH="${CMAKE_PREFIX_PATH:-}:$PREFIX/lib/cmake:$PREFIX/lib64/cmake:$PREFIX/lib:$PREFIX/lib64:$PREFIX"
export CMAKE_PREFIX_PATH
# PKG_CONFIG_PATH="${PKG_CONFIG_PATH:-}:$PREFIX/lib/pkgconfig:$PREFIX/lib64/pkgconfig"
# export PKG_CONFIG_PATH
# LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:$PREFIX/lib:$PREFIX/lib64"
# export LD_LIBRARY_PATH

rm -rf build
mkdir -p build
cd build
# cmake $CMAKE_PARAMS ..
cmake .. -DCMAKE_EXPORT_COMPILE_COMMANDS=On -DWITH_AWS=On -DUSE_RTTI=On -DCMAKE_BUILD_TYPE=Release 
make -j20


# my
# cmake .. -DCMAKE_EXPORT_COMPILE_COMMANDS=On -DWITH_AWS=On -DUSE_RTTI=On -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="/home/wjp/CacheLib/opt/cachelib"
# sudo ln -s /home/wjp/CacheLib/cachelib/cmake/FindSodium.cmake /usr/local/share/cmake-3.17/Modules