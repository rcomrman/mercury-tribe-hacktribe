/* Comparator only, isolated QEMU RAM. Does not call LCD sender. */
#define main r9_unused_main
#define R9_CASE (2500+CASE)
#include "../recovery_r9/lcd.c"
#undef main
int main(void){
 init();emit(0,0,0);
 for(unsigned page=0;page<8;page++){
  unsigned changed=compare(page,CASE?1:0);
  CHECK(changed==(CASE?1u:0u),210);emit(10+page,changed,page);
 }
 guards();emit(20,0,0);return 0;
}
