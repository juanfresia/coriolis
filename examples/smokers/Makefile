CFLAGS := -g
VFLAGS := --leak-check=full --show-leak-kinds=all --track-origins=yes
ARCHIVOS = lock.o semaphore.o log.o
PROGRAMA = main

all: clean $(PROGRAMA)

$(PROGRAMA): $(ARCHIVOS) $(PROGRAMA).o
	@mkdir -p fifos
	@mkdir -p locks
	@rm -f fifos/*
	gcc -o $(PROGRAMA) $^

run: clean $(PROGRAMA)
	./$(PROGRAMA)

%.o: %.c
	gcc $(CFLAGS) -c $< -o $@ 

clean:
	rm -f $(PROGRAMA) *.o
	rm -f fifos/*
	rm -f locks/*
	touch makefile~
	rm *~

valgrind: clean $(PROGRAMA)
	valgrind $(VFLAGS) ./$(PROGRAMA)

.PHONY: clean


