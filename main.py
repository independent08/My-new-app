import os  ## zaimportowanie biblioteki
#pip install streamlit - instalacja biblioteki streamlit
# print(1)  ## wypisanie w konsoli
# print(1+1)

a = 1 + 2  ## przypisanie do zmiennej a   
def dodaj(x,y): ## stworzenie funkcji
    return x + y

# print(dodaj(3, 4))
# print(dodaj(a, 4))

##lista
zasady_azotowe = ["adenina", "guanina", "cytozyna", "tynina", "uracyl"] ## kwadratowy nawias =  lista (mozna ją edytować)
print(zasady_azotowe)
print(zasady_azotowe[0]) # 0- dostęp do pierwszego elementu zbioru czyli w tym przypadku adenina
for zasada in zasady_azotowe: ##pętla for
    print("Zasada azotowa:", zasada)





#krotka - tupla ()
koordynaty = (10, 20, 30, 40) ##nie można jej potem edytować
print(koordynaty)
print(koordynaty[1]) # wypisanie drugiego elementu
#pętla for
for punkt in koordynaty: 
 print("Punkt koordynaty:", punkt)




#słownik - dict
osoba = {"imie": "Jan",            # "imie", "nazwisko", "wiek" to są klucze słownika
         "nazwisko": "kowalski",   #"Jan", "Kowalski", "30" to są wartości w słowniku
         "wiek": 30}
print(osoba)
print(osoba["nazwisko"])
#pętla po kluczach - domyśłna pętla w słowniku
for klucz in osoba:
    print("Klucz:", klucz)
#pętla po wartościach
for wartosc in osoba.values():
    print("Wartość:", wartosc)
#pętla po kluczach i wartościach
for klucz, wartosc in osoba.items():
    print("Klucz:", klucz, "Wartość:", wartosc)

print("----",">>>>>")
print("----"+">>>>>") # + łączy dwa stringii bez spacji
print("""
to jest
wielolinijkowy
ciąg
znaków
      """)

      
#zbiór - set (kasuje duplikaty)
liczby = {1, 2, 3, 4, 5, 5 ,5, 5}
print(liczby)
print(7 in liczby) ## sprawdzenie czy ty w tym zbiorze jest liczba 7

for liczba in liczby:
    print("Liczba:", liczba)

#pętla range() - liczba elementów
for a in range(5): #domyśłnie idzie co jeden
    print("Iteracja:", a)

for a in range(1,10,2): #tutaj idzie co dwa, bo używamy trzeciego parametru "2"
    print("Iteracja:", a)
    if a > 5:
        print("Ta liczba jest większa od 5:", a)
    else:
        print("Ta liczba jest mniejsza lub rówa 5:", a)





#pętla while (działa dopoki warunek jest prawdziwy)
i = 0
while i < 5:
    print("while iteracja:", i)
    i += 1 #dodaje do każdego przekręcenia pętli 1 do i