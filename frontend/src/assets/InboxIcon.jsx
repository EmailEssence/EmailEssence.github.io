// eslint-disable-next-line react/prop-types
export default function SvgComponent({color}) {
  return (
    <svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M3 12h5.5l1.5 3h4l2-3h5M3 12v6a2 2 0 002 2h14a2 2 0 002-2v-6M3 12l2.757-7.351A1 1 0 016.693 4h10.614a1 1 0 01.936.649L21 12"
        stroke={color}
        strokeLinecap="round"
        strokeWidth="1.5"
      />
    </svg>
  );
}
