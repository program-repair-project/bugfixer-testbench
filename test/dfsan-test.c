#include <sanitizer/dfsan_interface.h>
#include <stdio.h>
#include <assert.h>

int main(void) {
  int i = 100;
  int j = 200;
  int k = 300;
  dfsan_label i_label = dfsan_create_label("i", 0);
  dfsan_label j_label = dfsan_create_label("j", 0);
  dfsan_label k_label = dfsan_create_label("k", 0);
  dfsan_set_label(i_label, &i, sizeof(i));
  dfsan_set_label(j_label, &j, sizeof(j));
  dfsan_set_label(k_label, &k, sizeof(k));

  int z = j + 10;
  dfsan_label z_label = dfsan_get_label(z);
  // check whether the value of i goes to z
  printf("%d\n", dfsan_has_label(z_label, i_label));
  // check whether the value of j goes to z
  printf("%d\n", dfsan_has_label(z_label, j_label));
  // check whether the value of k goes to z
  printf("%d\n", dfsan_has_label(z_label, k_label));
  return 0;
}
