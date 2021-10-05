htmx.on("htmx:beforeSend", function(evt){
  NProgress.configure({ trickleSpeed: 100 });
  NProgress.start();
  NProgress.set(0.4);
});
htmx.on("htmx:afterOnLoad", function(evt){
  NProgress.done();
});
