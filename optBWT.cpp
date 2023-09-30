#include <iostream>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <string>
#include <map>
#include <stack>
#include <algorithm>

using namespace std;

char C[] = {'$', 'A', 'C', 'G', 'T'};

/////// open files SA and LCP ///////
int open(char *arq, int n, int *ARQ){
    FILE* f = fopen(arq, "rb"); // rb to binary files
    int ret = fread(ARQ, sizeof(int), n, f);
    if(ret+1 != n){
        printf("Error reading file %s\n", arq);
    }
    fclose(f);
    return *ARQ;
}

int decide(stack < map <char, int> > Parikh, int dna[]){
    int cont = 2;
    while(cont >= 2 && !Parikh.empty()){
        map <char, int> a_Parikh = {{'$',0}, {'A',0}, {'C',0}, {'G',0}, {'T',0}};
        a_Parikh = Parikh.top();
        Parikh.pop();
        cont = 0;
        //'$', 'A', 'C', 'G', 'T'
        for(char c : C){
            if(a_Parikh[c] > 0 &&  dna[c] > 0){
                cont++;
                dna[c]++;
            }
        }
    }
    int *m = max_element(dna, dna+5);
    for(int i  = 0; i < 5; i++){
        if(m == (int*)dna[i]) return i;
    }
    return '0'; 
}

char unstack(stack < map <char, int> > Parikh, map <char, int> a_Parikh, map <char, int> top_Parikh, char optBWT[], int p, int i, int b){
    do{
        int j = 0;
        int k = i-1;

        for(char c : C){
            while(j < a_Parikh[c] && p != c){
                optBWT[k] = c;
                j++;
                k--;
            }
            b = b-a_Parikh[c];
            j = 0;
        }
        if(p != '0'){
            while(j < top_Parikh[p]+a_Parikh[p]){//inserir a quantidade de cada um dos vetores do caractere correspondente
                optBWT[k] = p;
                j++;
                k--;
            }
            top_Parikh[p] = 0;
        }
        //zerar a contagem do vetor
        for(char c : C)
            a_Parikh[c] = 0;

        if(!Parikh.empty()){ //desempilhar e decidir a ordem dos caracteres
            a_Parikh = top_Parikh;
            top_Parikh = Parikh.top();
            Parikh.pop();
            int cont = 0;
            int dna[] = {0, 0, 0, 0, 0};

            //'$', 'A', 'C', 'G', 'T'
            for(char c : C){
                if(a_Parikh[c] > 0 && top_Parikh[c] > 0){
                    cont++;
                    dna[c]++;
                }
            }
            
            if(cont >= 2 && !Parikh.empty()) p = decide(Parikh, dna);
            else if(dna['$'] > 0) p = '$'; 
            else if(dna['A'] > 0) p = 'A'; 
            else if(dna['C'] > 0) p = 'C'; 
            else if(dna['G'] > 0) p = 'G'; 
            else if(dna['T'] > 0) p = 'T'; 
            else p = '0'; 
        }
        else{
            j = 0;
            int posi = top_Parikh['$']+top_Parikh['A']+top_Parikh['C']+top_Parikh['G']+top_Parikh['T'];
            if(top_Parikh[optBWT[k-posi-1]] > 0){
                p = optBWT[k-posi-1];
            }
            for(char c : C){
                while(j < top_Parikh[c] && p != c){
                    optBWT[k] = c;
                    j++;
                    k--;
                }
                b = b-top_Parikh[c];
                j = 0;
            }
            if(p != '0'){
                while(j < top_Parikh[p]+a_Parikh[p]){//inserir a quantidade de cada um dos vetores do caractere correspondente
                    optBWT[k] = p;
                    j++;
                    k--;
                }
                top_Parikh[p] = 0;
            }
        }
        return *optBWT;
    }while(!Parikh.empty());
}

int main(int argc, char *argv[]){
    
    long int n = 0;
    
    FILE* f = fopen(argv[2], "rb"); // rb to binary files
    fseek(f, 0, SEEK_END);
    n = ftell(f) + 1; 
    rewind(f);
    char *BWT = new char[n+1];
    char *optBWT = new char[n+1];
    int ret = fread(BWT, sizeof(char), n, f);
    BWT[n]='\0';
    if(ret+1 != n){
        printf("Error reading file %s\n", argv[1]);
    }
    fclose(f);

    int *SA = new int[n+1];
    open(argv[3], n, SA);
    int *LCP = new int[n+1];
    open(argv[4], n, LCP);
    int *ISA = new int[n+1];
    open(argv[5], n, ISA);
    
    /////// SAP //////
    bool *SAP = new bool[n+1];
    SAP[0] = 0;
    SAP[1] = 0;
    for(int i = 2; i < n; i++){
        if(BWT[ISA[SA[i]+LCP[i]+1]]== '$'){
            SAP[i] = 1;
        }
        else{
            SAP[i] = 0;
        }
    }

    // Implementação do optBWT //

    char *file_optBWT = new char[strlen(argv[1])+8];
    strcpy(file_optBWT, argv[1]);
    strcat(file_optBWT, ".optBWT");
    f = fopen(file_optBWT, "wb");
    stack < map <char, int> > Parikh;

    map <char, int> top_Parikh = {{'$',0}, {'A',0}, {'C',0}, {'G',0}, {'T',0}};
    map <char, int> a_Parikh = {{'$',0}, {'A',0}, {'C',0}, {'G',0}, {'T',0}};

    int y = 0, j = 0;
    int p = '0';
    int a = 0; //início do intervalo
    int b = 0; //fim do intervalo

    for(int i = 0; i < n-1; i++){
        // Primeiro passo: encontrar um intervalo
        int inter = 0;
    
        if(SAP[i] == 0 && (i == n-1 || SAP[i+1] == 0)){
            optBWT[i] = BWT[i]; //optBWT igual ao BWT
            b = i-1;
            if(!Parikh.empty()){
                a_Parikh = Parikh.top();
                Parikh.pop();
                int j = 0;
                if(a_Parikh[optBWT[i]] > 0){
                    p = optBWT[i];
                    int k = i-1;
                    while(j < a_Parikh[p]){
                        optBWT[k] = p;
                        j++;
                        k--;
                    }
                    b = b-a_Parikh[optBWT[i]];
                    a_Parikh[optBWT[i]] = 0;
                    p = '0';
                }
                *optBWT = unstack(Parikh, a_Parikh, top_Parikh, optBWT, p, i-j, b);
            }
        }
        else if(SAP[i] == 1 && SAP[i-1] == 0){
            a = i-1;
            a_Parikh[BWT[i-1]] += 1; //Calculo do vetor Parikh
            p = BWT[i-1]; //armazena o primeiro caractere do intervalo para verificar se o intervalo é interessante
            while(SAP[i] == 1){
                a_Parikh[BWT[i]] += 1; //Calculo do vetor Parikh
                if(p != BWT[i]){ //se houver 2 caracteres diferentes
                    inter += 1; //o intervalo é interessante
                }
                i++;
            }
            b = i-1; //intevalo: [a, b] 
            j = a;
            if(Parikh.empty()){ //se a pilha estiver vazia
                if(inter == 0){ //se o intervalo não é interessante
                    while(j <= b){
                        optBWT[j] = BWT[j]; //escrevendo os valores da optBWT no intervalo
                        j++;
                    }
                    //zerar a contagem do vetor
                    for(char c : C)
                        a_Parikh[c] = 0; 
                }
                else if(a_Parikh[optBWT[j-1]] > 0 && (j-1) > 0){ //se o último caractere da optBWT for igual a um caractere do intervalo
                    int y = a;
                    int k = 0;
                    while(k < a_Parikh[optBWT[j-1]]){
                        optBWT[y] = optBWT[j-1]; // escrevendo o último caractere do intervalo
                        y++;
                        k++;
                    }
                    a_Parikh[optBWT[j-1]] = 0;
                    Parikh.push(a_Parikh); //restante do vetor Parikh inserido na pilha
                }
                else{
                    Parikh.push(a_Parikh); //vetor Parikh inserido na pilha
                }
            }        
            else if(!Parikh.empty()){
                top_Parikh = Parikh.top();
                Parikh.pop();
                int cont = 0;
                //'$', 'A', 'C', 'G', 'T'
                for(char c : C){
                    if(a_Parikh[c] > 0 && top_Parikh[c] > 0){
                        cont++;
                        p = c;
                    }
                }
                if(cont >= 2){
                    Parikh.push(a_Parikh); //vetor Parikh inserido na pilha
                }
                else{ //1 caractere correspondente, desempilhar
                    *optBWT = unstack(Parikh, a_Parikh, top_Parikh, optBWT, p, i, b);
                }
            }
            i--;
        }
        //zerar a contagem do vetor
        for(char c : C)
            a_Parikh[c] = 0;
        top_Parikh = a_Parikh;
    }

    for(int i = 0; i < n-1; i++){
        printf("\n %d %d %c %c", i, SAP[i], BWT[i], optBWT[i]);
        fprintf(f, "%c\n", optBWT[i]);
    }
    printf("\n");
    delete [] optBWT;
    delete [] BWT;
    delete [] SA;
    delete [] ISA;
    delete [] LCP;
    delete [] SAP;

    fclose(f);
}