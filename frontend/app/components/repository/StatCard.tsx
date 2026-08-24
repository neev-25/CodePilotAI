interface Props {
  label: string;
  value: string | number;
  color?: string;
}

export default function StatCard({ label, value, color = "text-gray-900" }: Props) {
  return (
    <div className="border rounded-xl p-5 bg-white">
      <h3 className="text-gray-500 text-sm">{label}</h3>
      <p className={`text-3xl font-bold mt-2 ${color}`}>{value}</p>
    </div>
  );
}
