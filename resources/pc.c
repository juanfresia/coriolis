#include<stdio.h>

// @has_checkpoints

int main(){
  int pid = 8;
  for(int i=0; i<10;i++) {
    printf("Producing %d", i);
    // @checkpoint produce pid i
  }

  for(int j=0; j<10;j++) {
    printf("Consuming %d", j);
    // @checkpoint consume pid j
  }
 
  return 0;
}
