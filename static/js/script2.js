// Flaskから渡されたデータ
let allStudyDays = studyDays;  // 日付リスト
let allStudyTimes = studyTimes;  // 各日付に対応する勉強時間

// グラフのインスタンスを保持
let studyTimeChart = null;

// グラフの描画関数
function renderChart() {
    let ctx = document.getElementById("studyTimeChart").getContext("2d");

    // すでにグラフが存在する場合、削除
    if (studyTimeChart) {
        studyTimeChart.destroy();  // 前のグラフを削除
    }

    // 新しいグラフを描画
    studyTimeChart = new Chart(ctx, {
        type: 'bar',  // 棒グラフ
        data: {
            labels: allStudyDays,  // x軸に日付を表示
            datasets: [{
                label: "勉強時間 (分)",
                data: allStudyTimes,  // 勉強時間
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true  // y軸の最小値を0に設定
                }
            }
        }
    });
}

// 「次の週」ボタンをクリック
document.getElementById('nextWeekButton').addEventListener('click', function() {
    const params = new URLSearchParams(window.location.search);
    const currentOffset = parseInt(params.get('week_offset')) || 0;
    params.set('week_offset', currentOffset + 1);  // 次の週にスライド
    window.location.href = window.location.pathname + '?' + params.toString();
});

// 「前の週」ボタンをクリック
document.getElementById('prevWeekButton').addEventListener('click', function() {
    const params = new URLSearchParams(window.location.search);
    const currentOffset = parseInt(params.get('week_offset')) || 0;
    params.set('week_offset', currentOffset - 1);  // 前の週にスライド
    window.location.href = window.location.pathname + '?' + params.toString();
});

// 初期描画
renderChart();
