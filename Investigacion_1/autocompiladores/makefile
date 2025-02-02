PROGRAMA = app
OBJETOS = main.o
CC = gcc
CFLAGS = -Wall -Wextra -std=c11

$(PROGRAMA): $(OBJETOS)
	$(CC) $(OBJETOS) -o $(PROGRAMA)

main.o: main.c platform.h
	$(CC) $(CFLAGS) -c main.c

config_autocomp:
	@if [ "$(OS)" = "Linux" ]; then \
		echo "Compilando para Linux"; \
		CFLAGS += -DLINUX; \
	elif [ "$(OS)" = "Windows" ]; then \
		echo "Compilando para Windows"; \
		CFLAGS += -DWINDOWS; \
	fi

clean:
	rm -f $(OBJETOS) $(PROGRAMA)
