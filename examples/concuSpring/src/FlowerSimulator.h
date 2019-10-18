#ifndef FLOWER_SIMULATOR_H
#define FLOWER_SIMULATOR_H

#define INPUT_BUFFER 256

class FlowerSimulator {
    private:
        bool pause;
        bool quit;

        std::string configPath;
        std::string logLevel;


    public:
        FlowerSimulator(const std::string &, const std::string &);
        virtual ~FlowerSimulator();

        void start(void);
};


#endif // FLOWER_SIMULATOR_H
