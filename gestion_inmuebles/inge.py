numero = 42
texto = "manzanas"
resultado = numero + texto 
print(resultado)  #Da error al ser fuertemente tipado.
resultado = str(numero) + " " + texto
print(resultado) #Esta es una posible solución del error, aplicando reglas de conversión.