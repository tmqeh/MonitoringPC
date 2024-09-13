Grafana version
onpre : 6.6.0
AWS : 7.5.2

Export 는 "Export for sharing externally" 옵션으로함
(__inputs, __requires 부분이 추가됨)

비교 예시 
daily check-* (external)
daily check-no_external (no external)

변수 핸들링에 쓰이는 옵션 (매우 유용함)
https://grafana.com/docs/grafana/latest/variables/advanced-variable-format-options/



JSON Export할 때
Export for sharing externally 옵션을 사용하면
새로운 Grafana에서도 DB 매핑을 쉽게 할 수 있음
(없으면 각 쿼리별로 수동으로 매핑해주고 있으면 Import할 때 통으로 지정해줌)




손쉬운 Export 참고 (제대로 안되지만 (버전 다르면 발생하는 문제로 보임) 같은버전에 활용 가능할듯)

http://10.7.7.42:3000/api/search
http://10.7.7.42:3000/api/search?folderIds=4

http://10.7.7.42:3000/api/search?folderIds=9&query=&starred=false

http://10.7.7.42:3000/api/dashboards/uid/87mh18_Gk/

curl -H "Authorization: Bearer eyJrIjoiSzJ3UWZQcURSZmhKQVhxTDFqRlVZQ0NQajFXYUJZZkYiLCJuIjoiZXhwb3J0X0pTT04iLCJpZCI6MX0=" http://10.7.7.42:3000/api/dashboards/uid/ZL5v6lsZk > daily-check.json