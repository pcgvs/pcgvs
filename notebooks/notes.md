Se non erro, i nodi colorati allo stesso modo dovrebbero partire allo stesso momento.

L(q)-coloring: assegniamo numeri naturali ai nodi in modo che nodi adiacenti abbiano sempre dei numeri la cui differenza in valore assoluto è maggiore o uguale a q. Lo scopo è quello di far si che la differenza tra il numero massimo assegnato ed il minimo assegnato sia la più piccola possibile. 

Ad ogni iterazione, i nodi sono ordinati in maniera decrescente per saturazione, il nodo con più saturazione è colorato con il colore corrente

I colori dei nodi sono le posizioni temporali dove i corrispondenti tubi saranno posizionati. 

Il grado di saturazione di un sub-node $v_i^s$ è indicato con $S(v_i^s)$ calcolato come la somma di:

+ $S_d(v_i^s)$ Saturation degree tradizionale (numero di colori differenti in nodi adiacenti)
+ $S_l(v_i^s)$ La durata relativa
+ $S_{app}(v_i^s)$ Tempo di apparizione
+ $S_{pc}(v_i^s)$ Numero di potenziali collisioni

Sia $L_i$ la durata del tubo $T_i$, e siano $M$ i tubi in totale, allora calcoliamo la durata relativa
$$
S_l (v_i^s) = \frac{L_i}{\max_{k=1, \dots,M} L_k}
$$
Sia $N$ il numero totale di frame, allora calcoliamo il tempo di apparizione $S_{app}$
$$
S_{app}(v_i^s) = \frac{N - t_i^s}{N}
$$
Per calcolare $S_{pc}$ contiamo il numero di subnodes all'interno dello stesso mainnode con $v_i^s$ e controlliamo il peso con cui $v_i^s$ è connesso: 
$$
S_{pc}(v_i^s) = ...
$$
Bisogna **normalizzare** $S_d$ e $S_{pc}$ per il numero  

$v_i$ per $i=1, \dots, n$ sono gli s-node e gli m-node isolati. Constraints: 

1. Nodi connessi da edge unidirezionali devono essere colorati 



Algoritmo: 

1. Inizializza il colore al minimo valore
2. Inizializza i flag $f_i$ di tipo 
3. Inizializza i flag $f_i^c$ (colorato o meno)
4. Calcola la saturazione di ogni nodo 
   1. Ad ogni iterazione dovrà essere ricalcolata solo $S_d$
5. Ordina i nodi per saturazione decrescente
   1. In caso di parità vince chi appare prima
6. Colora i nodi in ordine finché alcun nodo può essere colorato
   1. Se viene colorato un s-node, colorare gli s-node collegati
7. Aumentare il colore di 1 e ripetere dal passo 4













