// script.js
document.addEventListener('DOMContentLoaded', function() {
  // Flask から渡された変数を使ってグラフを描画
  let ctx = document.getElementById('studyTimeChart').getContext('2d');
  
  let studyTimeChart = new Chart(ctx, {
      type: 'bar',  // グラフのタイプ（棒グラフ）
      data: {
          labels: ['Today', 'This Week', 'This Month'],
          datasets: [{
              label: 'Study Time (Minutes)',
              data: [dailyTime, weeklyTime, monthlyTime],  // Flask から渡された勉強時間のデータ
              backgroundColor: ['blue', 'green', 'red'],  // 各バーの色
              borderColor: ['blue', 'green', 'red'],  // 枠線の色
              borderWidth: 1
          }]
      },
      options: {
          scales: {
              y: {
                  beginAtZero: true  // y軸は0から始める
              }
          }
      }
  });

  // 週のグラフを表示するボタンのクリックイベント
  document.getElementById('weekButton').addEventListener('click', function() {
      studyTimeChart.data.datasets[0].data = [dailyTime, weeklyTime, 0]; // 週のデータを表示
      studyTimeChart.update();  // グラフを更新
  });

  // 月のグラフを表示するボタンのクリックイベント
  document.getElementById('monthButton').addEventListener('click', function() {
      studyTimeChart.data.datasets[0].data = [dailyTime, 0, monthlyTime]; // 月のデータを表示
      studyTimeChart.update();  // グラフを更新
  });
});
