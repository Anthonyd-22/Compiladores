#ifdef _WIN32
    #define PLATFORM "Windows"
    #define OS_SPECIFIC_FUNCTION "Hola mundo windows"
#elif __linux__
    #define PLATFORM "Linux"
    #define OS_SPECIFIC_FUNCTION "Hola mundo linux"
#else
    #define PLATFORM "Desconocido"
    #define OS_SPECIFIC_FUNCTION "Hola mundo desconocido"
#endif
