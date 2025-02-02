PROGRAMA = holamundo

OBJETOS = main.o mensaje.o

CC = gcc

CFLAGS = -Wall -Wextra -std=c11

$(PROGRAMA): $(OBJETOS)
	$(CC) $(OBJETOS) -o $(PROGRAMA)

main.o: main.c mensaje.h
	$(CC) $(CFLAGS) -c main.c

mensaje.o: mensaje.c mensaje.h
	$(CC) $(CFLAGS) -c mensaje.c

clean:
	rm -f $(OBJETOS) $(PROGRAMA)
