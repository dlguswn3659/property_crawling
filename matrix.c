#include <stdio.h>

#define ROWS 3
#define COLS 3
#define MAX_TERMS 10

// 행렬의 곱셈
#define ROWS_A 3
#define COLS_A 2
#define ROWS_B 2
#define COLS_B 4

typedef struct {
    int row;
    int col;
    int value;
} term;

term a[MAX_TERMS];

typedef struct SparseMatrix {
    term data[MAX_TERMS];
    int rows;   //행의 개수
    int cols;   //열의 개수
    int terms;  //항의 개수
} SparseMatrix;

void sparse_matrix_add1(int A[ROWS][COLS], int B[ROWS][COLS], int C[ROWS][COLS]){
    int r, c;
    for(r = 0; r < ROWS; r++){
        for(c = 0; c < COLS; c++){
            C[r][c] = A[r][c] + B[r][c];
        }
    }
} // C = A + B 

void sparse_matrix_multi1(int A[ROWS_A][COLS_A], int B[COLS_B][ROWS_B], int C[ROWS_A][COLS_B]){
    for(int i = 0; i < ROWS_A; i++) {
        for(int j = 0; j < COLS_B; j++) {
            C[i][j] = 0;
            for (int k = 0; k < COLS_A; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        } 
    }
}

SparseMatrix sparse_matrix_add2(SparseMatrix a, SparseMatrix b){
    SparseMatrix c;
    int ca=0, cb=0, cc=0;   // 각 배열의 항목을 가리키는 인덱스
    // 배열 a와 배열 b의 크기가 같은지를 확인

    if( a.rows != b.rows || a.cols != b.cols ){
        fprintf(stderr, "희소행렬 크기에러\n");
        exit(1);
    }
    c.rows = a.rows;
    c.cols = a.cols;
    c.terms = 0;    // 항의 개수

    while( ca < a.terms && cb < b.terms ){
        // 각 항목의 순차적인 번호를 계산한다.
        int inda = a.data[ca].row * a.cols + a.data[ca].col;
        int indb = b.data[cb].row * b.cols + b.data[cb].col;
        if(inda < indb){
            // a 배열 하목이 앞에 있으면
            c.data[cc++] = a.data[ca++];
        }
        else if(inda == indb){
            //a와 b가 같은 위치
            if (a.data[ca].value + b.cata[cb].value != 0){
                c.data[cc].row = a.data[ca].row;
                c.data[cc].col = a.data[ca].col;
                c.data[cc++].value = a.data[ca++].value + b.data[cb++].value;
            }
            else {
                ca++; cb++;
            }
        }
        else {
            c.data[cc++] = b.data[cb++];
        }
    }
    // 배열 a와 b에 남아 있는 항들을 배열 c로 옮긴다.
    for(; ca < a.terms; ){
        c.data[cc++] = a.data[ca++];
    }
    for(; cb < b.terms; ){
        c.data[cc++] = b.data[cb++];
    }
    c.terms = cc;
    return c;
}

SparseMatrix sparse_matrix_multi2(SparseMatrix a, SparseMatrix b){
    SparseMatrix c;
    int ca=0, cb=0, cc=0;   // 각 배열의 항목을 가리키는 인덱스
    int tmpc_col, tmpc_row, tmpc_val;
    // 배열 a와 배열 b의 크기가 같은지를 확인

    if( a.cows != b.rows ){
        fprintf(stderr, "희소행렬 크기에러\n");
        exit(1);
    }
    c.rows = a.rows;
    c.cols = b.cols;
    c.terms = 0;    // 항의 개수
    int find_same = 0;

    for(ca = 0; ca < a.terms; ca++){
        for(cb = 0; cb < b.terms; cb++){
            find_same = 0;
            if(a.data[ca].col == b.data[cb].row){
                if(c.terms >= 1){
                    for(int c_ind = 0; c_ind < c.terms; c_ind++){   //c 애들 중에 r, c가 같은 애들은 value 더하고 없애주기
                        if((c.data[c_ind].row == a.data[ca].row) &&(c.data[c_ind].col == b.data[cb].col)){
                            c.data[c_ind].value = c.data[c_ind].value + (a.data[ca].value*b.data[cb].value);
                            find_same = 1;
                            break;
                        }
                    }
                    if(find_same == 0){ // 만약 중첩이 없으면 새로 넣어주기
                        c.data[cc].row = a.data[ca].row;
                        c.data[cc].col = b.data[cb].col;
                        c.data[cc].value = a.data[ca].value*b.data[cb].value;
                        c.terms++;
                        cc++;
                    }
                }else{   
                    c.data[cc].row = a.data[ca].row;
                    c.data[cc].col = b.data[cb].col;
                    c.data[cc].value = a.data[ca].value*b.data[cb].value;
                    c.terms++;
                }
            }
        }
    }     
    return c;
}

int main() {
    SparseMatrix m1 = { {{1, 1, 5},{2, 2, 9}}, 3, 3, 2 };
    SparseMatrix m2 = { {{0, 0, 5},{2, 2, 9}}, 3, 3, 2 };
    SparseMatrix m3;

    m3 = sparse_matrix_add2(m1, m2);
}