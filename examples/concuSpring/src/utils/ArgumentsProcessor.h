#ifndef ARGUMENTS_PROCESSOR__H
#define ARGUMENTS_PROCESSOR__H

#include <string>

class ArgumentsProcessor {
    private:
    public:
        ArgumentsProcessor();
        ~ArgumentsProcessor();

        // Parametros:
        //      - path: path to config file
        //      - logLevel: level of detail in logs
        // Devuelve 0 en caso de exito y no se debe continuar ejecutando el programa
        // Devuelve 1 en caso de exito y se debe continuar ejecutando el programa
        // Devuelve -1 en caso de falla
        int processArguments(int argc, char * argv[], std::string &, std::string & logLevel);

        // Imprime informacion sobre la version del programa
        void version(void);

        // Imprime informacion sobre como invocar el programa
        void help(void);
};


#endif // ARGUMENTS_PROCESSOR__H
