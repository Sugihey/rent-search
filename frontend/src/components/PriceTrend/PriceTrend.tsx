import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface PriceTrendData {
  date: string;
  avg_price: number;
  min_price: number;
  max_price: number;
  count: number;
}

const PriceTrend = () => {
  const [priceTrendData, setPriceTrendData] = useState<PriceTrendData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState<string>('30');

  useEffect(() => {
    const fetchPriceTrendData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/api/price-trends?days=${period}`);
        if (!response.ok) {
          throw new Error(`API request failed with status ${response.status}`);
        }
        const data = await response.json();
        setPriceTrendData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
        console.error('Error fetching price trend data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPriceTrendData();
  }, [period]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  const formatYAxis = (value: number) => {
    return `${value}万円`;
  };

  const formatTooltip = (value: number) => {
    return [`${value}万円`];
  };

  const formatCountTooltip = (value: number) => {
    return [`${value}件`];
  };

  const formattedData = priceTrendData.map(item => ({
    ...item,
    formattedDate: formatDate(item.date)
  }));

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>不動産価格の推移</CardTitle>
        <Tabs defaultValue="30" onValueChange={setPeriod}>
          <TabsList>
            <TabsTrigger value="7">7日間</TabsTrigger>
            <TabsTrigger value="30">30日間</TabsTrigger>
            <TabsTrigger value="180">180日間</TabsTrigger>
            <TabsTrigger value="365">365日間</TabsTrigger>
          </TabsList>
        </Tabs>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center items-center h-80">
            <p>データを読み込み中...</p>
          </div>
        ) : error ? (
          <div className="flex justify-center items-center h-80">
            <p className="text-red-500">エラー: {error}</p>
          </div>
        ) : priceTrendData.length === 0 ? (
          <div className="flex justify-center items-center h-80">
            <p>データがありません</p>
          </div>
        ) : (
          <div className="space-y-8">
            <div className="h-80">
              <h3 className="text-lg font-medium mb-2">価格推移</h3>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={formattedData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="formattedDate" />
                  <YAxis tickFormatter={formatYAxis} />
                  <Tooltip 
                    formatter={formatTooltip}
                    labelFormatter={(label) => `日付: ${label}`}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="avg_price"
                    name="平均価格"
                    stroke="#8884d8"
                    activeDot={{ r: 8 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="min_price"
                    name="最低価格"
                    stroke="#82ca9d"
                  />
                  <Line
                    type="monotone"
                    dataKey="max_price"
                    name="最高価格"
                    stroke="#ff7300"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            
            <div className="h-80">
              <h3 className="text-lg font-medium mb-2">物件数</h3>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={formattedData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="formattedDate" />
                  <YAxis />
                  <Tooltip 
                    formatter={formatCountTooltip}
                    labelFormatter={(label) => `日付: ${label}`}
                  />
                  <Legend />
                  <Bar
                    dataKey="count"
                    name="物件数"
                    fill="#8884d8"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PriceTrend;
