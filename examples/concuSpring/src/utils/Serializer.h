//
// Created by demian on 14/9/19.
//

#ifndef TP1_FIUBA_CONCURRENTE_SERIALIZER_H
#define TP1_FIUBA_CONCURRENTE_SERIALIZER_H

#include <Concurrentes.h>

class Serializer {

public:

    Serializer(bool bIsReading) : bIsReading(bIsReading) {}
    virtual ~Serializer() {}

    inline bool isReading() { return bIsReading; }
    inline bool isWriting() { return !bIsReading; }

    inline Serializer& operator<<(char& value)
    {
        this->serialize(&value, sizeof(char));
        return *this;
    }

    inline Serializer& operator<<(float& value)
    {
        this->serialize(&value, sizeof(float));
        return *this;
    }

    inline Serializer& operator<<(double& value)
    {
        this->serialize(&value, sizeof(double));
        return *this;
    }

    inline Serializer& operator<<(unsigned int& value)
    {
        this->serialize(&value, sizeof(unsigned int));
        return *this;
    }

    inline Serializer& operator<<(int& value)
    {
        this->serialize(&value, sizeof(int));
        return *this;
    }

    template<typename T>
    inline Serializer& operator<<(T& enumType)
    {
        static_assert(std::is_enum<T>::value , "This template function is valid only for enums types");
        this->serialize(&enumType, sizeof(T));
        return *this;
    }

    inline Serializer& operator<<(unsigned long& value)
    {
        this->serialize(&value, sizeof(unsigned long));
        return *this;
    }

    inline Serializer& operator<<(long& value)
    {
        this->serialize(&value, sizeof(long));
        return *this;
    }

    inline Serializer& operator<<(std::string& value)
    {
        //Serialize the string size first
        unsigned long stringSize = value.size() + 1;
        this->operator<<(stringSize);

        char str[stringSize];

        if(isWriting())
        {
            strcpy(str, value.c_str());
        }

        this->serialize(str, stringSize);

        if(isReading())
        {
            value = std::string(str);
        }

        return *this;
    }

    virtual void serialize(void * data,  size_t count) = 0;

protected:

    bool bIsReading;
};


#endif //TP1_FIUBA_CONCURRENTE_SERIALIZER_H
