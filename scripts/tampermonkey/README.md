### Detect Ctrl+Key
```javascript
document.addEventListener('keydown', function(event) {
  if (event.ctrlKey && event.key === 'z') {
    alert('Undo!');
  }
});
```
Using event.key greatly simplifies the code, removing hardcoded constants. It has support for IE 9+.</br>
Additionally, using document.addEventListener means you won’t clobber other listeners to the same event.</br>
Finally, there is no reason to use window.event. It’s actively discouraged and can result in fragile code.</br>
Or:
```javascript
$(document).keydown(function(e){
  if( e.which === 89 && e.ctrlKey ){
     alert('control + y'); 
  }
  else if( e.which === 90 && e.ctrlKey ){
     alert('control + z'); 
  }          
});
```
### Keycode Table
| Key  | Code | ==== | ==== | ==== | ==== |
|----:|:----|----:|:----|----:|:----|
|  backspace | 8| d | 68| numpad 6 | 102|
|  tab | 9| e | 69| numpad 7 | 103|
|  enter | 13| f | 70| numpad 8 | 104|
|  shift | 16| g | 71| numpad 9 | 105|
|  ctrl | 17| h | 72| multiply | 106|
|  alt | 18| i | 73| add(+) | 107|
|  pause/break | 19| j | 74| subtract(-) | 109|
|  caps lock | 20| k | 75| decimal point(.) | 110|
|  escape | 27| l | 76| divide(/) | 111|
|  page up | 33| m | 77| f1 | 112|
|  page down | 34| n | 78| f2 | 113|
|  end | 35| o | 79| f3 | 114|
|  home | 36| p | 80| f4 | 115|
|  left arrow | 37| q | 81| f5 | 116|
|  up arrow | 38| r | 82| f6 | 117|
|  right arrow | 39| s | 83| f7 | 118|
|  down arrow | 40| t | 84| f8 | 119|
|  insert | 45| u | 85| f9 | 120|
|  delete | 46| v | 86| f10 | 121|
|  0 | 48| w | 87| f11 | 122|
|  1 | 49| x | 88| f12 | 123|
|  2 | 50| y | 89| num lock | 144|
|  3 | 51| z | 90| scroll lock | 145|
|  4 | 52| left window key | 91| semi-colon(;) | 186|
|  5 | 53| right window key | 92| equal sign(=) | 187|
|  6 | 54| select key | 93| comma(,) | 188|
|  7 | 55| numpad 0 | 96| dash(-) | 189|
|  8 | 56| numpad 1 | 97| period(.) | 190|
|  9 | 57| numpad 2 | 98| forward slash(\) | 191|
|  a | 65| numpad 3 | 99| open bracket(\[) | 219|
|  b | 66| numpad 4 | 100| close bracket(\]) | 221|
|  c | 67| numpad 5 | 101| back slash(/) | 220|
|      |     |  grave accent(\`) | 192| single quote(') | 222|




