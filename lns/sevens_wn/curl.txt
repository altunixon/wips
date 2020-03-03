for i in $(curl https://yoraikun.wordpress.com/7s-chapters/ | tr '"' '\n' | grep 'sevens-' | sort | grep '^http.*/$'); do
      o=$(echo $i | awk -F '/' '{print $(NF-1)".htm"}'); 
      curl $i | sed -n '/class="entry-content"/,/\.entry-content/p' > $o;
done
